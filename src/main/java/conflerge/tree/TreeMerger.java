package conflerge.tree;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.utils.Pair;

import conflerge.ConflergeUtil;
import conflerge.tree.visitor.MergeVisitor;
import conflerge.tree.visitor.NodeListUnwrapperVisitor;
import conflerge.tree.visitor.NodeListWrapperVisitor;

/**
 * Merges Java files by AST. Represents the base, local, and remote 
 * files to be merged. The merge method attempts to perform a merge, returning 
 * a node that it the root of the merged tree on success, and null on failure.
 */
public class TreeMerger {

    /**
     * ASTs parsed from the base, local, and remote files.
     */
    private Node base;
    private Node local;
    private Node remote;
    
    /**
     * The imports that will be included in the resulting merge, if successful.
     * Contains the union of import declarations from local and remote.
     */
    private List<ImportDeclaration> imports;
    
    /**
     * Constructs a new TreeMerger for merging the given files.
     * 
     * @param baseFile
     * @param localFile
     * @param remoteFile
     * @throws FileNotFoundException
     */
    public TreeMerger(String baseFile, String localFile, String remoteFile) throws FileNotFoundException {
        this.base = JavaParser.parse(new File(baseFile));
        this.local = JavaParser.parse(new File(localFile));
        this.remote = JavaParser.parse(new File(remoteFile));
        
        this.imports = mergeImports((CompilationUnit) local, (CompilationUnit) remote);
        
        removeImports((CompilationUnit) base);
        removeImports((CompilationUnit) local);
        removeImports((CompilationUnit) remote);
    }

    /**
     * Perform the merge operation on this TreeMerger's base, local, and remote files.
     * 
     * @return A merged AST iff no conflicts were detected, otherwise null.
     */
    public Node merge() {      
        base.accept(new NodeListWrapperVisitor(), "A"); 
        local.accept(new NodeListWrapperVisitor(), "B");
        remote.accept(new NodeListWrapperVisitor(), "C");
        
        DiffResult localDiff = new TreeDiffer(base, local).diff();
        DiffResult remoteDiff = new TreeDiffer(base, remote).diff();
        
        ConflergeUtil.conflict = false;
        ConflergeUtil.commentConflict = false;
        
        Pair<DiffResult, DiffResult> diffs = new Pair<>(localDiff, remoteDiff);
        base.accept(new MergeVisitor(), diffs);   
        
        if (ConflergeUtil. conflict) {
            return null;
        }
        
        base.accept(new NodeListUnwrapperVisitor(), null); 
        
        addImports((CompilationUnit) base, imports);
        
        return base;
    }
    
    /**
     * @param local
     * @param remote
     * @return The union of local and remote's import declarations, sorted alphabetically.
     */
    public static List<ImportDeclaration> mergeImports(CompilationUnit local, CompilationUnit remote) {
        List<ImportDeclaration> imports = new ArrayList<>(local.getImports());
        for (ImportDeclaration imprt : remote.getImports()) {
            if (!imports.contains(imprt)) {
                imports.add(imprt);
            }
        }
        Collections.sort(imports, new Comparator<ImportDeclaration>() {
            @Override
            public int compare(ImportDeclaration o1, ImportDeclaration o2) {
                return o1.toString().compareTo(o2.toString());
            }
        });
        return imports;
    }
    
    /**
     * Adds the given import declarations to the given CompilationUnit.
     * 
     * @param cu
     * @param imports
     */
    public static void addImports(CompilationUnit cu, List<ImportDeclaration> imports) {
        for (ImportDeclaration imprt : imports) {
            ((CompilationUnit) cu).addImport(imprt);
        } 
    }
    
    /**
     * Removes all import declarations from the given CompilationUnit.
     * 
     * @param cu
     */
    public static void removeImports(CompilationUnit cu) {
        cu.getImports().clear();
    }

}
