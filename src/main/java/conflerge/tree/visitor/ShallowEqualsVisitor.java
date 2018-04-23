package conflerge.tree.visitor;

import com.github.javaparser.ast.ArrayCreationLevel;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.AnnotationDeclaration;
import com.github.javaparser.ast.body.AnnotationMemberDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.EmptyMemberDeclaration;
import com.github.javaparser.ast.body.EnumConstantDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.InitializerDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.comments.BlockComment;
import com.github.javaparser.ast.comments.JavadocComment;
import com.github.javaparser.ast.comments.LineComment;
import com.github.javaparser.ast.expr.ArrayAccessExpr;
import com.github.javaparser.ast.expr.ArrayCreationExpr;
import com.github.javaparser.ast.expr.ArrayInitializerExpr;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.BooleanLiteralExpr;
import com.github.javaparser.ast.expr.CastExpr;
import com.github.javaparser.ast.expr.CharLiteralExpr;
import com.github.javaparser.ast.expr.ClassExpr;
import com.github.javaparser.ast.expr.ConditionalExpr;
import com.github.javaparser.ast.expr.DoubleLiteralExpr;
import com.github.javaparser.ast.expr.EnclosedExpr;
import com.github.javaparser.ast.expr.FieldAccessExpr;
import com.github.javaparser.ast.expr.InstanceOfExpr;
import com.github.javaparser.ast.expr.IntegerLiteralExpr;
import com.github.javaparser.ast.expr.LambdaExpr;
import com.github.javaparser.ast.expr.LongLiteralExpr;
import com.github.javaparser.ast.expr.MarkerAnnotationExpr;
import com.github.javaparser.ast.expr.MemberValuePair;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.MethodReferenceExpr;
import com.github.javaparser.ast.expr.Name;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.NormalAnnotationExpr;
import com.github.javaparser.ast.expr.NullLiteralExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.expr.SimpleName;
import com.github.javaparser.ast.expr.SingleMemberAnnotationExpr;
import com.github.javaparser.ast.expr.StringLiteralExpr;
import com.github.javaparser.ast.expr.SuperExpr;
import com.github.javaparser.ast.expr.ThisExpr;
import com.github.javaparser.ast.expr.TypeExpr;
import com.github.javaparser.ast.expr.UnaryExpr;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.stmt.AssertStmt;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.BreakStmt;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.stmt.ContinueStmt;
import com.github.javaparser.ast.stmt.DoStmt;
import com.github.javaparser.ast.stmt.EmptyStmt;
import com.github.javaparser.ast.stmt.ExplicitConstructorInvocationStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.ForStmt;
import com.github.javaparser.ast.stmt.ForeachStmt;
import com.github.javaparser.ast.stmt.IfStmt;
import com.github.javaparser.ast.stmt.LabeledStmt;
import com.github.javaparser.ast.stmt.LocalClassDeclarationStmt;
import com.github.javaparser.ast.stmt.ReturnStmt;
import com.github.javaparser.ast.stmt.SwitchEntryStmt;
import com.github.javaparser.ast.stmt.SwitchStmt;
import com.github.javaparser.ast.stmt.SynchronizedStmt;
import com.github.javaparser.ast.stmt.ThrowStmt;
import com.github.javaparser.ast.stmt.TryStmt;
import com.github.javaparser.ast.stmt.WhileStmt;
import com.github.javaparser.ast.type.ArrayType;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.IntersectionType;
import com.github.javaparser.ast.type.PrimitiveType;
import com.github.javaparser.ast.type.TypeParameter;
import com.github.javaparser.ast.type.UnionType;
import com.github.javaparser.ast.type.UnknownType;
import com.github.javaparser.ast.type.VoidType;
import com.github.javaparser.ast.type.WildcardType;
import com.github.javaparser.ast.visitor.GenericVisitor;
import com.github.javaparser.ast.visitor.Visitable;

import conflerge.tree.ast.NodeListWrapperNode;


/**
 * This class checks for shallow equality, necessary in the tree diffing algorithm.
 * Most nodes are shallowly equal if they are instances of the same class. Nodes that
 * have values, like those corresponding literal primitives or identifiers, are only
 * shallowly equal if their values are equal.
 * 
 * Returns true iff a both nodes have the same type and value (if any).
 */
@SuppressWarnings("deprecation")
public class ShallowEqualsVisitor implements GenericVisitor<Boolean, Visitable> {

    private static final ShallowEqualsVisitor SINGLETON = new ShallowEqualsVisitor();

    public static boolean equals(final Node n1, final Node n2) {
        return SINGLETON.nodeEquals(n1, n2);
    }

    private ShallowEqualsVisitor() { }

    private <T extends Node> boolean nodeEquals(final T n1, final T n2) {
        if (n1 == n2) return true;    
        if (n1 == null || n2 == null) return false;
        if (n1.getClass() != n2.getClass()) return false;
        if (n1 instanceof NodeListWrapperNode && n2 instanceof NodeListWrapperNode) return true;
        return n1.accept(this, n2);
    }
    
    public Boolean visit(final NodeListWrapperNode n1, final Visitable arg) {
        return true;
    }

    private boolean objEquals(final Object n1, final Object n2) {
        if (n1 == n2) {
            return true;
        }
        if (n1 == null || n2 == null) {
            return false;
        }
        return n1.equals(n2);
    }

    @Override
    public Boolean visit(final CompilationUnit n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final PackageDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final TypeParameter n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final LineComment n1, final Visitable arg) {
        final LineComment n2 = (LineComment) arg;
        if (!objEquals(n1.getContent(), n2.getContent()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final BlockComment n1, final Visitable arg) {
        final BlockComment n2 = (BlockComment) arg;
        if (!objEquals(n1.getContent(), n2.getContent()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final ClassOrInterfaceDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final EnumDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final EnumConstantDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final AnnotationDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final AnnotationMemberDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final FieldDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final VariableDeclarator n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ConstructorDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final MethodDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final Parameter n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final EmptyMemberDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final InitializerDeclaration n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final JavadocComment n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ClassOrInterfaceType n1, final Visitable arg) {
        return n1.getElementType().equals(((ClassOrInterfaceType)arg).getElementType());
    }

    @Override
    public Boolean visit(final PrimitiveType n1, final Visitable arg) {
        final PrimitiveType n2 = (PrimitiveType) arg;
        if (!objEquals(n1.getType(), n2.getType()))
          return false;
        return true;
    }

    @Override
    public Boolean visit(ArrayType n1, Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(ArrayCreationLevel n1, Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final IntersectionType n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final UnionType n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(VoidType n1, Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final WildcardType n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final UnknownType n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ArrayAccessExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ArrayCreationExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ArrayInitializerExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final AssignExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final BinaryExpr n1, final Visitable arg) {
        return n1.getOperator().equals(((BinaryExpr)arg).getOperator());
    }

    @Override
    public Boolean visit(final CastExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ClassExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ConditionalExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final EnclosedExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final FieldAccessExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final InstanceOfExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final StringLiteralExpr n1, final Visitable arg) {
        final StringLiteralExpr n2 = (StringLiteralExpr) arg;
        if (!objEquals(n1.getValue(), n2.getValue()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final IntegerLiteralExpr n1, final Visitable arg) {
        final IntegerLiteralExpr n2 = (IntegerLiteralExpr) arg;
        if (!objEquals(n1.getValue(), n2.getValue()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final LongLiteralExpr n1, final Visitable arg) {
        final LongLiteralExpr n2 = (LongLiteralExpr) arg;
        if (!objEquals(n1.getValue(), n2.getValue()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final CharLiteralExpr n1, final Visitable arg) {
        final CharLiteralExpr n2 = (CharLiteralExpr) arg;
        if (!objEquals(n1.getValue(), n2.getValue()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final DoubleLiteralExpr n1, final Visitable arg) {
        final DoubleLiteralExpr n2 = (DoubleLiteralExpr) arg;
        if (!objEquals(n1.getValue(), n2.getValue()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final BooleanLiteralExpr n1, final Visitable arg) {
        final BooleanLiteralExpr n2 = (BooleanLiteralExpr) arg;
        if (!objEquals(n1.getValue(), n2.getValue()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final NullLiteralExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final MethodCallExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final NameExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ObjectCreationExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final Name n1, final Visitable arg) {
        final Name n2 = (Name) arg;
        if (!objEquals(n1.getIdentifier(), n2.getIdentifier()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(SimpleName n1, Visitable arg) {
        final SimpleName n2 = (SimpleName) arg;
        if (!objEquals(n1.getIdentifier(), n2.getIdentifier()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final ThisExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final SuperExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final UnaryExpr n1, final Visitable arg) {
        final UnaryExpr n2 = (UnaryExpr) arg;
        if (!objEquals(n1.getOperator(), n2.getOperator()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final VariableDeclarationExpr n1, final Visitable arg) {
        final VariableDeclarationExpr n2 = (VariableDeclarationExpr) arg;
        if (!objEquals(n1.getModifiers(), n2.getModifiers()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final MarkerAnnotationExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final SingleMemberAnnotationExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final NormalAnnotationExpr n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final MemberValuePair n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ExplicitConstructorInvocationStmt n1, final Visitable arg) {
        final ExplicitConstructorInvocationStmt n2 = (ExplicitConstructorInvocationStmt) arg;
        if (!objEquals(n1.isThis(), n2.isThis()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(final LocalClassDeclarationStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final AssertStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final BlockStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final LabeledStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final EmptyStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ExpressionStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final SwitchStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final SwitchEntryStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final BreakStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ReturnStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final IfStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final WhileStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ContinueStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final DoStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ForeachStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ForStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ThrowStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final SynchronizedStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final TryStmt n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final CatchClause n1, final Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(LambdaExpr n1, Visitable arg) {
        final LambdaExpr n2 = (LambdaExpr) arg;
        if (!objEquals(n1.isEnclosingParameters(), n2.isEnclosingParameters()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(MethodReferenceExpr n1, Visitable arg) {
        final MethodReferenceExpr n2 = (MethodReferenceExpr) arg;
        if (!objEquals(n1.getIdentifier(), n2.getIdentifier()))
            return false;
        return true;
    }

    @Override
    public Boolean visit(TypeExpr n1, Visitable arg) {
        return true;
    }

    @Override
    public Boolean visit(final ImportDeclaration n1, final Visitable arg) {
        final ImportDeclaration n2 = (ImportDeclaration) arg;
        if (!objEquals(n1.isAsterisk(), n2.isAsterisk()))
            return false;
        if (!objEquals(n1.isStatic(), n2.isStatic()))
            return false;
        return true;
    }

    @SuppressWarnings({ "rawtypes" })
    @Override
    public Boolean visit(NodeList n, Visitable arg) {
        return true;
    }
}
